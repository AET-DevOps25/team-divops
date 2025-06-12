import {
  Anchor,
  Button,
  Container,
  Group,
  Paper,
  PasswordInput,
  Stack,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import { isEmail, useForm } from "@mantine/form";
import { useNavigate } from "react-router";

const Login = () => {
  const navigate = useNavigate();
  const form = useForm({
    mode: "uncontrolled",
    initialValues: {
      email: "",
      password: "",
    },
    validate: {
      email: isEmail("Invalid email"),
      password: (value) => (value ? null : "Password Required"),
    },
  });
  console.log(form.errors);
  const login = () => {
    // TODO call backend
    navigate("/main");
  };

  return (
    <Container size={420} my={40}>
      <form onSubmit={form.onSubmit(login)}>
        <Stack>
          <Title ta="center">Welcome back!</Title>

          <Text ta="center">
            Do not have an account yet?{" "}
            <Anchor href="signup">Create account</Anchor>
          </Text>
        </Stack>

        <Paper withBorder shadow="sm" p={22} mt={30} radius="md">
          <Stack gap="sm">
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
            <Group justify="space-between" mt="lg">
              <Anchor component="button" size="sm">
                Forgot password?
              </Anchor>
            </Group>
            <Button type="submit" fullWidth mt="xl" radius="md">
              Sign in
            </Button>
          </Stack>
        </Paper>
      </form>
    </Container>
  );
};

export default Login;
