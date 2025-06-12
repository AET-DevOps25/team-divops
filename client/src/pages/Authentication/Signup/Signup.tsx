import {
  Anchor,
  Button,
  Container,
  Paper,
  PasswordInput,
  Stack,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import { isEmail, isNotEmpty, useForm } from "@mantine/form";
import { useNavigate } from "react-router";

const Signup = () => {
  const navigate = useNavigate();

  const form = useForm({
    mode: "uncontrolled",
    initialValues: {
      name: "",
      email: "",
      password: "",
    },
    validate: {
      name: isNotEmpty("Name Required"),
      email: isEmail("Invalid email"),
      password: isNotEmpty("Password Required"),
    },
  });

  const signup = () => {
    // TODO call backend
    navigate("/login");
  };

  return (
    <Container size={420} my={40}>
      <form onSubmit={form.onSubmit(signup)}>
        <Stack>
          <Title ta="center">Hello!</Title>

          <Text ta="center">
            Already have an account? <Anchor href="signup">Login</Anchor>
          </Text>
        </Stack>
        <Paper withBorder shadow="sm" p={22} mt={30} radius="md">
          <Stack gap="sm">
            <TextInput
              withAsterisk
              label="Name"
              placeholder="John Doe"
              key={form.key("name")}
              {...form.getInputProps("name")}
            />
            <TextInput
              withAsterisk
              label="Email"
              placeholder="your@email.com"
              key={form.key("email")}
              {...form.getInputProps("email")}
            />
            <PasswordInput
              withAsterisk
              label="Password"
              placeholder="Your password"
              key={form.key("password")}
              {...form.getInputProps("password")}
            />
            <Button type="submit" fullWidth mt="xl" radius="md">
              Sign Up
            </Button>
          </Stack>
        </Paper>
      </form>
    </Container>
  );
};

export default Signup;
